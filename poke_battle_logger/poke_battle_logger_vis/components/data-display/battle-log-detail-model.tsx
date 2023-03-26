import {
  Card,
  Heading,
  CardBody,
  Flex,
  Text,
  Badge,
  Divider,
  Editable,
  EditableTextarea,
  EditablePreview,
} from '@chakra-ui/react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  AspectRatio,
} from '@chakra-ui/react';
import { TimeIcon } from '@chakra-ui/icons';
import PokemonIcon from '../atoms/pokemon-icon';
import ReactPlayer from 'react-player/youtube'

interface BattleLogDetailModalProps {
    isOpen: boolean;
    onClose: () => void;
  battle_id: string;
  battle_created_at: string;
  win_or_lose: string;
  next_rank: number;
  your_pokemon_team: string;
  opponent_pokemon_team: string;
  your_pokemon_select1: string;
  your_pokemon_select2: string;
  your_pokemon_select3: string;
  opponent_pokemon_select1: string;
  opponent_pokemon_select2: string;
  opponent_pokemon_select3: string;
  memo: string;
  video: string;
}

const BattleLogDetailModal: React.FunctionComponent<
  BattleLogDetailModalProps
> = ({
    isOpen,
    onClose,
  battle_id,
  battle_created_at,
  win_or_lose,
  next_rank,
  your_pokemon_team,
  opponent_pokemon_team,
  your_pokemon_select1,
  your_pokemon_select2,
  your_pokemon_select3,
  opponent_pokemon_select1,
  opponent_pokemon_select2,
  opponent_pokemon_select3,
  memo,
  video,
}) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} size={"xl"}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>対戦詳細</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
        <ReactPlayer url={video} controls={true} width={"100%"}/>
          <Text>
            <TimeIcon boxSize={4} margin={'5px'} />
            {battle_created_at}
          </Text>
          <Text>
            {win_or_lose === 'win' ? (
              <Badge colorScheme="green">勝利！</Badge>
            ) : (
              <Badge colorScheme="red">負け</Badge>
            )}{' '}
            → 👑 {next_rank}
          </Text>
          <Divider margin={'5px'} />
          <Heading size={'xs'}>ShowDown</Heading>
          <Flex>
            {your_pokemon_team.split(',').map((pokemon_name) => (
              <PokemonIcon
                key={pokemon_name}
                pokemon_name={pokemon_name}
                boxSize={'40px'}
              />
            ))}
          </Flex>
          <Text>VS</Text>
          <Flex>
            {opponent_pokemon_team.split(',').map((pokemon_name) => (
              <PokemonIcon
                key={pokemon_name}
                pokemon_name={pokemon_name}
                boxSize={'40px'}
              />
            ))}
          </Flex>
          <Divider margin={'5px'} />
          <Heading size={'xs'}>Selection</Heading>
          <Flex>
            <PokemonIcon pokemon_name={your_pokemon_select1} boxSize={'50px'} />
            <PokemonIcon pokemon_name={your_pokemon_select2} boxSize={'50px'} />
            <PokemonIcon pokemon_name={your_pokemon_select3} boxSize={'50px'} />
          </Flex>
          <Text>VS</Text>
          <Flex>
            <PokemonIcon
              pokemon_name={opponent_pokemon_select1}
              boxSize={'50px'}
            />
            <PokemonIcon
              pokemon_name={opponent_pokemon_select2}
              boxSize={'50px'}
            />
            <PokemonIcon
              pokemon_name={opponent_pokemon_select3}
              boxSize={'50px'}
            />
          </Flex>
          <Divider margin={'5px'} />
          <Heading size={'xs'}>📝 Memo</Heading>
          <Editable defaultValue={memo}>
            <EditablePreview />
            <EditableTextarea />
          </Editable>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default BattleLogDetailModal;